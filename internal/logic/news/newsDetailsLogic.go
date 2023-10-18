package news

import (
	"context"
	"errors"
	"strings"
	"time"

	"news/internal/svc"
	"news/internal/types"
	"news/model"

	"github.com/zeromicro/go-zero/core/logx"
)

type NewsDetailsLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

func NewNewsDetailsLogic(ctx context.Context, svcCtx *svc.ServiceContext) *NewsDetailsLogic {
	return &NewsDetailsLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *NewsDetailsLogic) NewsDetails(req *types.NewsDetailsReq) (any, error) {
	uuid := strings.TrimSpace(req.ArticleUUID)
	article, err := l.svcCtx.ArticleModel.FindByUuid(l.ctx, uuid)
	if errors.Is(err, model.ErrNotFound) {
		return nil, errors.New("data does not exist")
	} else if err != nil {
		logx.Error(err)
		return nil, errors.New("server error")
	}
	article.RawUid = ""
	article.Id = 0
	article.TextContent.String = ""
	article.CategoryId = 0
	article.CreateAt = time.Time{}
	article.UpdateAt = time.Time{}
	article.PublishAt = time.Now()
	return article, nil
}
