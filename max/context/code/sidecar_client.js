// node.script HTTP client. Does not call LiveAPI.
const http = require("http");

const HOST = "127.0.0.1";
let port = Number(process.env.CONTEXT_SIDECAR_PORT || 8765);

function request(method, path, body) {
  return new Promise(function (resolve, reject) {
    const payload = body ? Buffer.from(JSON.stringify(body)) : null;
    const req = http.request(
      {
        host: HOST,
        port: port,
        path: path,
        method: method,
        headers: payload
          ? {
              "Content-Type": "application/json",
              "Content-Length": String(payload.length)
            }
          : {}
      },
      function (res) {
        const chunks = [];
        res.on("data", function (chunk) {
          chunks.push(chunk);
        });
        res.on("end", function () {
          const text = Buffer.concat(chunks).toString("utf8");
          try {
            resolve({ status: res.statusCode, body: JSON.parse(text) });
          } catch (error) {
            resolve({ status: res.statusCode, body: { ok: false, error: text } });
          }
        });
      }
    );
    req.on("error", function () {
      resolve({ status: 0, body: { ok: false, error: "sidecar_down" } });
    });
    if (payload) {
      req.write(payload);
    }
    req.end();
  });
}

function health() {
  request("GET", "/health").then(function (result) {
    outlet(0, JSON.stringify(result.body));
  });
}

function intent(jsonText) {
  let body;
  try {
    body = JSON.parse(jsonText);
  } catch (error) {
    outlet(0, JSON.stringify({ ok: false, error: "invalid json" }));
    return;
  }
  request("POST", "/intent", body).then(function (result) {
    outlet(0, JSON.stringify(result.body));
  });
}

function setport(value) {
  port = Number(value || 8765);
}
