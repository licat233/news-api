package model

import (
	"context"
	"database/sql"
	"fmt"
	"strings"

	"github.com/Masterminds/squirrel"
	"github.com/zeromicro/go-zero/core/stores/cache"
	"github.com/zeromicro/go-zero/core/stores/sqlc"
	"github.com/zeromicro/go-zero/core/stores/sqlx"
	"github.com/zeromicro/go-zero/core/stringx"
)

var _ ArticleModel = (*customArticleModel)(nil)
var cacheArticleUuidPrefix = "cache:news:article:uuid:"
var articlePublicRows = strings.Join(stringx.Remove(articleFieldNames, "`id`", "`create_at`", "`create_time`", "`created_at`", "`update_at`", "`update_time`", "`updated_at`"), ",")

type (
	// ArticleModel is an interface to be customized, add more methods here,
	// and implement the added methods in customArticleModel.
	ArticleModel interface {
		articleModel  // extended interface by gozero
		article_model // extended interface by genzero
		Flow(ctx context.Context, categoryId int64, offset, pageSize uint64) ([]*Article, error)
		More(ctx context.Context, categoryId int64, limit uint64) ([]*Article, error)
	}

	customArticleModel struct {
		*defaultArticleModel
	}
)

// NewArticleModel returns a model for the database table.
func NewArticleModel(conn sqlx.SqlConn, c cache.CacheConf, opts ...cache.Option) ArticleModel {
	cacheArticleIdPrefix = "cache:news:article:id:" // modifying cache id prefix by genzero
	return &customArticleModel{
		defaultArticleModel: newArticleModel(conn, c, opts...),
	}
}

func (m *customArticleModel) Delete(ctx context.Context, id int64) error {
	articleIdKey := fmt.Sprintf("%s%v", cacheArticleIdPrefix, id)
	keys := []string{articleIdKey}
	article, err := m.FindOne(ctx, id)
	if err != nil && err != ErrNotFound {
		return err
	} else if err == nil {
		uuid := article.Uuid
		articleUuidKey := fmt.Sprintf("%s%v", cacheArticleUuidPrefix, uuid)
		keys = append(keys, articleUuidKey)
	}
	_, err = m.ExecCtx(ctx, func(ctx context.Context, conn sqlx.SqlConn) (result sql.Result, err error) {
		query := fmt.Sprintf("delete from %s where `id` = ?", m.table)
		return conn.ExecCtx(ctx, query, id)
	}, keys...)
	return err
}

func (m *customArticleModel) Insert(ctx context.Context, data *Article) (sql.Result, error) {
	articleIdKey := fmt.Sprintf("%s%v", cacheArticleIdPrefix, data.Id)
	articleUuidKey := fmt.Sprintf("%s%v", cacheArticleUuidPrefix, data.Uuid)
	ret, err := m.ExecCtx(ctx, func(ctx context.Context, conn sqlx.SqlConn) (result sql.Result, err error) {
		query := fmt.Sprintf("insert into %s (%s) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", m.table, articleRowsExpectAutoSet)
		return conn.ExecCtx(ctx, query, data.Uuid, data.RawUid, data.Title, data.CategoryId, data.PublishAt, data.Author, data.Cover, data.TextContent, data.HtmlContent, data.ViewsCount, data.Tags)
	}, articleIdKey, articleUuidKey)
	return ret, err
}

func (m *customArticleModel) Update(ctx context.Context, data *Article) error {
	articleIdKey := fmt.Sprintf("%s%v", cacheArticleIdPrefix, data.Id)
	articleUuidKey := fmt.Sprintf("%s%v", cacheArticleUuidPrefix, data.Uuid)
	_, err := m.ExecCtx(ctx, func(ctx context.Context, conn sqlx.SqlConn) (result sql.Result, err error) {
		query := fmt.Sprintf("update %s set %s where `id` = ?", m.table, articleRowsWithPlaceHolder)
		return conn.ExecCtx(ctx, query, data.Uuid, data.RawUid, data.Title, data.CategoryId, data.PublishAt, data.Author, data.Cover, data.TextContent, data.HtmlContent, data.ViewsCount, data.Tags, data.Id)
	}, articleIdKey, articleUuidKey)
	return err
}

func (m *customArticleModel) Flow(ctx context.Context, categoryId int64, offset, pageSize uint64) ([]*Article, error) {
	sq := squirrel.Select(articleRows).From(m.table).Where("status=1").Offset(offset).Limit(pageSize).OrderBy("publish_at DESC")
	if categoryId > 0 {
		//分类
		sq = sq.Where(squirrel.Eq{"category_id": categoryId})
	}
	query, agrs, err := sq.ToSql()
	if err != nil {
		return nil, err
	}
	var data []*Article
	err = m.QueryRowsNoCacheCtx(ctx, &data, query, agrs...)
	return data, err
}

func (m *customArticleModel) More(ctx context.Context, categoryId int64, limit uint64) ([]*Article, error) {
	sq := squirrel.Select(articleRows).From(m.table).Where("status=1").Limit(limit).OrderBy("RAND()")
	if categoryId > 0 {
		//分类
		sq = sq.Where(squirrel.Eq{"category_id": categoryId})
	}
	query, agrs, err := sq.ToSql()
	if err != nil {
		return nil, err
	}
	var data []*Article
	err = m.QueryRowsNoCacheCtx(ctx, &data, query, agrs...)
	return data, err
}

func (m *customArticleModel) FindByUuid(ctx context.Context, uuid string) (*Article, error) {
	articleUuidKey := fmt.Sprintf("%s%v", cacheArticleUuidPrefix, uuid)
	var resp Article
	err := m.QueryRowCtx(ctx, &resp, articleUuidKey, func(ctx context.Context, conn sqlx.SqlConn, v any) error {
		query := fmt.Sprintf("select %s from %s where `uuid` = ? limit 1", articleRows, m.table)
		return conn.QueryRowCtx(ctx, v, query, uuid)
	})
	switch err {
	case nil:
		return &resp, nil
	case sqlc.ErrNotFound:
		return nil, ErrNotFound
	default:
		return nil, err
	}
}
