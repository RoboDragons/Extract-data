//フロントエンド（HTML + JavaScript）
@RestController
@RequestMapping("/frontend")
public class FrontendController {
    @GetMapping("/upload")
    public String uploadPage() {
        return "<!DOCTYPE html>\n" +
                "<html lang='ja'>\n" +
                "<head>\n" +
                "    <meta charset='UTF-8'>\n" +
                "    <title>ファイルアップロード</title>\n" +
                "</head>\n" +
                "<body>\n" +
                "    <h2>ログファイルをアップロード</h2>\n" +
                "    <input type='file' id='fileInput'>\n" +
                "    <button onclick='uploadFile()'>アップロード</button>\n" +
                "    <pre id='output'></pre>\n" +
                "    <script>\n" +
                "        function uploadFile() {\n" +
                "            var file = document.getElementById('fileInput').files[0];\n" +
                "            var formData = new FormData();\n" +
                "            formData.append('file', file);\n" +
                "            fetch('/api/upload', {\n" +
                "                method: 'POST',\n" +
                "                body: formData\n" +
                "            })\n" +
                "            .then(response => response.json())\n" +
                "            .then(data => {\n" +
                "                document.getElementById('output').innerText = JSON.stringify(data, null, 2);\n" +
                "            })\n" +
                "            .catch(error => console.error('Error:', error));\n" +
                "        }\n" +
                "    </script>\n" +
                "</body>\n" +
                "</html>";
    }
}
