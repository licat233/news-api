package svc

import (
	"news/internal/config"
	"news/model"

	"github.com/zeromicro/go-zero/core/stores/sqlx"
)

type ServiceContext struct {
	Config        config.Config
	ArticleModel  model.ArticleModel
	ImageModel    model.ImageModel
	CategoryModel model.CategoryModel
}

func NewServiceContext(c config.Config) *ServiceContext {
	conn := sqlx.NewMysql(c.Mysql.DataSource)
	cacheConf := c.CacheRedis
	return &ServiceContext{
		Config:        c,
		ArticleModel:  model.NewArticleModel(conn, cacheConf),
		ImageModel:    model.NewImageModel(conn, cacheConf),
		CategoryModel: model.NewCategoryModel(conn, cacheConf),
	}
}
