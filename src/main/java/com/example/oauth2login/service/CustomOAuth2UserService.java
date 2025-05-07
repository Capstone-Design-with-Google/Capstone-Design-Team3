package com.example.oauth2login.service;

import com.example.oauth2login.domain.Member;
import com.example.oauth2login.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.DefaultOAuth2User;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService extends DefaultOAuth2UserService {

    private final MemberRepository memberRepository;

    @Override
    public OAuth2User loadUser(OAuth2UserRequest request) throws OAuth2AuthenticationException {
        OAuth2User oAuth2User = super.loadUser(request);
        Map<String, Object> attr = oAuth2User.getAttributes();

        String provider = request.getClientRegistration().getRegistrationId(); // google
        String providerId = (String) attr.get("sub");
        String email = (String) attr.get("email");
        String name = (String) attr.get("name");

        String loginId = provider + "_" + providerId;

        Member member = memberRepository.findByLoginId(loginId);
        if (member == null) {
            member = Member.builder()
                    .loginId(loginId)
                    .name(name)
                    .email(email)
                    .provider(provider)
                    .providerId(providerId)
                    .build();
            memberRepository.save(member);
        }

        return new DefaultOAuth2User(
                Collections.singleton(new SimpleGrantedAuthority("ROLE_USER")),
                attr,
                "sub"
        );
    }
}
