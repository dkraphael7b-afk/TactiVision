async function api(url, opcoes = {}) {
    const config = {...opcoes, headers: {...(opcoes.headers || {})}};
    if (opcoes.body && !(opcoes.body instanceof FormData)) config.headers["Content-Type"] = "application/json";
    try {
        const resposta = await fetch(url, config);
        let data = {};
        try { data = await resposta.json(); } catch {}
        if (resposta.status === 401 && !["/login", "/usuarios"].includes(url)) {
            if (!location.pathname.endsWith("/login.html")) location.href = "/frontend/login.html";
        }
        return {ok: resposta.ok, status: resposta.status, data};
    } catch (erro) {
        return {ok: false, status: 0, data: {detail: "Não foi possível conectar ao servidor."}};
    }
}
