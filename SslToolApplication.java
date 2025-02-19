//package com.example.ssltool;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.*;
import java.util.*;

@SpringBootApplication
@RestController
@RequestMapping("/api")
public class SslToolApplication {

    public static void main(String[] args) {
        SpringApplication.run(SslToolApplication.class, args);
    }

    @PostMapping("/upload")
    public Map<String, String> handleFileUpload(@RequestParam("file") MultipartFile file) {
        Map<String, String> response = new HashMap<>();
        try {
            // アップロードされたファイルを保存
            String filename = file.getOriginalFilename();
            Path filePath = Paths.get("uploads", filename);
            Files.createDirectories(filePath.getParent());
            Files.write(filePath, file.getBytes());

            // Pythonスクリプトを実行
            ProcessBuilder pb = new ProcessBuilder("python3", "gamedata.py", filePath.toString());
            pb.redirectErrorStream(true);
            Process process = pb.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                response.put("status", "success");
                response.put("data", output.toString());
            } else {
                response.put("status", "error");
                response.put("message", "Pythonスクリプトの実行に失敗しました。");
            }
        } catch (Exception e) {
            response.put("status", "error");
            response.put("message", e.getMessage());
            e.printStackTrace();  // エラーメッセージをログに出力
        }
        return response;
    }
}