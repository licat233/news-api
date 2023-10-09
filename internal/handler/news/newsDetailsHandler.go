package news

import (
	"net/http"

	"github.com/zeromicro/go-zero/rest/httpx"
	"news/internal/logic/news"
	"news/internal/svc"
	"news/internal/types"
)

func NewsDetailsHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req types.NewsDetailsReq
		if err := httpx.Parse(r, &req); err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}

		l := news.NewNewsDetailsLogic(r.Context(), svcCtx)
		resp, err := l.NewsDetails(&req)
		if err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
		} else {
			httpx.OkJsonCtx(r.Context(), w, resp)
		}
	}
}
