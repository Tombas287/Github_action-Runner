package com.example.news;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@SpringBootApplication
public class NewsFeedApplication {
    public static void main(String[] args) {
        SpringApplication.run(NewsFeedApplication.class, args);
    }

    @RestController
    class NewsController {
        @GetMapping("/news")
        public List<String> getNews() {
            return List.of(
                "Breaking: New Java release announced!",
                "Kubernetes becomes more popular for CI/CD",
                "Trivy scans Docker images for vulnerabilities"
            );
        }
    }
}