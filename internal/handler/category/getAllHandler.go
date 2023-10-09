package category

import (
	"net/http"

	"github.com/zeromicro/go-zero/rest/httpx"
	"news/internal/logic/category"
	"news/internal/svc"
)

func GetAllHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		l := category.NewGetAllLogic(r.Context(), svcCtx)
		resp, err := l.GetAll()
		if err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
		} else {
			httpx.OkJsonCtx(r.Context(), w, resp)
		}
	}
}
