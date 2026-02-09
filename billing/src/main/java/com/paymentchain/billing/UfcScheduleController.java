package com.paymentchain.billing;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/ufc")
public class UfcScheduleController {
    private final UfcSchedulePoster schedulePoster;

    public UfcScheduleController(UfcSchedulePoster schedulePoster) {
        this.schedulePoster = schedulePoster;
    }

    @PostMapping("/post")
    public ResponseEntity<String> postUpcomingEvents() {
        schedulePoster.postUpcomingEvents();
        return ResponseEntity.ok("UFC schedule posted if available.");
    }
}
