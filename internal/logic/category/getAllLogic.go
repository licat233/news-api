package category

import (
	"context"
	"errors"

	"news/internal/svc"

	"github.com/zeromicro/go-zero/core/logx"
)

type GetAllLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

func NewGetAllLogic(ctx context.Context, svcCtx *svc.ServiceContext) *GetAllLogic {
	return &GetAllLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *GetAllLogic) GetAll() (any, error) {
	data, err := l.svcCtx.CategoryModel.FindAll(l.ctx)
	if err != nil {
		logx.Error(err)
		return nil, errors.New("server error")
	}
	for i := range data {
		data[i].RawName = ""
		data[i].Id = 0
	}
	return data, nil
}
