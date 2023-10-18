package news

import (
	"context"
	"errors"
	"time"

	"news/internal/svc"
	"news/internal/types"
	"news/model"

	"github.com/zeromicro/go-zero/core/logx"
)

type NewsMoreLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

func NewNewsMoreLogic(ctx context.Context, svcCtx *svc.ServiceContext) *NewsMoreLogic {
	return &NewsMoreLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *NewsMoreLogic) NewsMore(req *types.NewsMoreReq) (any, error) {
	uuid := req.ArticleUUID
	var categoryId int64
	if uuid != "" {
		article, err := l.svcCtx.ArticleModel.FindByUuid(l.ctx, uuid)
		if errors.Is(err, model.ErrNotFound) {
			return []any{}, nil
		} else if err != nil {
			logx.Error(err)
			return nil, errors.New("server error")
		}
		categoryId = article.CategoryId
	}
	data, err := l.svcCtx.ArticleModel.More(l.ctx, categoryId, 10)
	if err != nil {
		logx.Error(err)
		return nil, errors.New("server error")
	}
	for i := range data {
		data[i].RawUid = ""
		data[i].TextContent.String = ""
		data[i].HtmlContent.String = ""
		data[i].Id = 0
		data[i].CategoryId = 0
		data[i].CreateAt = time.Time{}
		data[i].UpdateAt = time.Time{}
		data[i].PublishAt = time.Now()
	}
	return data, nil
}
