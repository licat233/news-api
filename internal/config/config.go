package config

import (
	"github.com/zeromicro/go-zero/core/stores/cache"
	"github.com/zeromicro/go-zero/rest"
)

type Config struct {
	rest.RestConf
	Mysql struct {
		DataSource string
	}

	AliOss struct {
		BucketName string
		Endpoint   string
		OssDomain  string
	}

	CacheRedis cache.CacheConf
}
