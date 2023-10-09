package model

import (
	"github.com/zeromicro/go-zero/core/stores/cache"
	"github.com/zeromicro/go-zero/core/stores/sqlx"
)

var _ ImageModel = (*customImageModel)(nil)

type (
	// ImageModel is an interface to be customized, add more methods here,
	// and implement the added methods in customImageModel.
	ImageModel interface {
		imageModel  // extended interface by gozero
		image_model // extended interface by genzero
	}

	customImageModel struct {
		*defaultImageModel
	}
)

// NewImageModel returns a model for the database table.
func NewImageModel(conn sqlx.SqlConn, c cache.CacheConf, opts ...cache.Option) ImageModel {
	cacheImageIdPrefix = "cache:news:image:id:" // modifying cache id prefix by genzero
	return &customImageModel{
		defaultImageModel: newImageModel(conn, c, opts...),
	}
}
