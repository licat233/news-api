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

type NewsFlowLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

func NewNewsFlowLogic(ctx context.Context, svcCtx *svc.ServiceContext) *NewsFlowLogic {
	return &NewsFlowLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *NewsFlowLogic) NewsFlow(req *types.NewsFlowReq) (any, error) {
	pageSize := req.PageSize
	if pageSize > 100 {
		pageSize = 100
	} else if pageSize <= 0 {
		pageSize = 10
	}

	offset := req.Length
	if offset < 0 {
		offset = 0
	}

	var categoryId int64
	uuid := req.CategoryUUID
	if uuid != "" {
		category, err := l.svcCtx.CategoryModel.FindByUuid(l.ctx, uuid)
		if err == model.ErrNotFound {
			return nil, errors.New("uuid does not exist")
		} else if err != nil {
			logx.Error(err)
			return nil, errors.New("server error")
		}
		categoryId = category.Id
	}

	data, err := l.svcCtx.ArticleModel.Flow(l.ctx, categoryId, uint64(offset), uint64(pageSize))
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
	}
	return data, nil
}
