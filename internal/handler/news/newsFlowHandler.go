package news

import (
	"net/http"

	"github.com/zeromicro/go-zero/rest/httpx"
	"news/internal/logic/news"
	"news/internal/svc"
	"news/internal/types"
)

func NewsFlowHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req types.NewsFlowReq
		if err := httpx.Parse(r, &req); err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}

		l := news.NewNewsFlowLogic(r.Context(), svcCtx)
		resp, err := l.NewsFlow(&req)
		if err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
		} else {
			httpx.OkJsonCtx(r.Context(), w, resp)
		}
	}
}
