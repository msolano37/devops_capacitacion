package com.paymentchain.billing;

import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class DiscordWebhookClient {
    private static final Logger LOGGER = LoggerFactory.getLogger(DiscordWebhookClient.class);

    private final RestTemplate restTemplate;
    private final String webhookUrl;

    public DiscordWebhookClient(RestTemplate restTemplate,
                                @Value("${discord.webhook-url:}") String webhookUrl) {
        this.restTemplate = restTemplate;
        this.webhookUrl = webhookUrl;
    }

    public void sendMessage(String message) {
        if (webhookUrl == null || webhookUrl.isBlank()) {
            LOGGER.warn("Discord webhook URL not configured. Skipping message.");
            return;
        }
        Map<String, String> payload = new HashMap<>();
        payload.put("content", message);
        restTemplate.postForEntity(webhookUrl, payload, String.class);
    }
}
