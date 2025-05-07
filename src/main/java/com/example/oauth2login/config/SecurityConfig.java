package com.example.oauth2login.config;

import com.example.oauth2login.service.CustomOAuth2UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final CustomOAuth2UserService customOAuth2UserService;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/user").authenticated()
                .anyRequest().permitAll())
            .oauth2Login(oauth -> oauth
                .defaultSuccessUrl("http://localhost:3000/oauth-redirect", true)
                .userInfoEndpoint(user -> user.userService(customOAuth2UserService)));

        return http.build();
    }
}
