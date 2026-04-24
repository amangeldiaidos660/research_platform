import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 25 },
    { duration: "1m", target: 100 },
    { duration: "30s", target: 0 }
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<1500"]
  }
};

const BASE_URL = __ENV.BASE_URL || "https://research-platform-seven.vercel.app";

export default function () {
  const responses = [
    http.get(`${BASE_URL}/`),
    http.get(`${BASE_URL}/api/v1/health`),
    http.get(`${BASE_URL}/api/v1/publications?q=mental%20health&limit=10`),
    http.get(`${BASE_URL}/api/v1/topics?limit=10`),
    http.get(`${BASE_URL}/analytics`)
  ];

  for (const response of responses) {
    check(response, {
      "status is 2xx": (r) => r.status >= 200 && r.status < 300
    });
  }

  sleep(1);
}
