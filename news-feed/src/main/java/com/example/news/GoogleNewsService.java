package com.example.news;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class GoogleNewsService {

    @Value("${serpapi.key}")
    private String apiKey;

    private final RestTemplate restTemplate = new RestTemplate();

    public Object getLatestNews(String query) {

        String url = String.format(
                "https://serpapi.com/search.json?q=%s&tbm=nws&api_key=%s",
                query,
                apiKey
        );

        Map<String, Object> response = restTemplate.getForObject(url, Map.class);

        return response.get("news_results"); // important for serpapi
    }
}