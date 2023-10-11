package news

import (
	"context"
	"errors"
	"strings"

	"news/internal/svc"
	"news/internal/types"
	"news/model"

	"github.com/zeromicro/go-zero/core/logx"
)

type FeedBackLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

func NewFeedBackLogic(ctx context.Context, svcCtx *svc.ServiceContext) *FeedBackLogic {
	return &FeedBackLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *FeedBackLogic) FeedBack(req *types.FeedBackReq) (any, error) {
	uuid := strings.TrimSpace(req.Uuid)
	if uuid != "" {
		return nil, errors.New("uuid can't be equal to empty")
	}
	article, err := l.svcCtx.ArticleModel.FindByUuid(l.ctx, uuid)
	if errors.Is(err, model.ErrNotFound) {
		return nil, errors.New("uuid does not exist")
	} else if err != nil {
		logx.Error(err)
		return nil, errors.New("server error")
	}
	// TODO: 进行一些文章处理，根据出入field进行字段处理
	switch req.Field {
	case "cover":
		//cover处理
		article.Cover = ""
	default:
		//article.status = 0
	}
	return nil, nil
}
