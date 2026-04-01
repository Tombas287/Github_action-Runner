package com.example.news;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class NewsController {

    private final GoogleNewsService newsService;

    public NewsController(GoogleNewsService newsService) {
        this.newsService = newsService;
    }

    @GetMapping("/")
    public String home(Model model) {
    model.addAttribute("techNews", newsService.getLatestNews("technology"));
    model.addAttribute("sportsNews", newsService.getLatestNews("sports"));
    model.addAttribute("businessNews", newsService.getLatestNews("business"));

    // ✅ New ones
    model.addAttribute("economyNews", newsService.getLatestNews("global economy"));
    model.addAttribute("warNews", newsService.getLatestNews("war conflict"));

    return "index";
}   

  
}