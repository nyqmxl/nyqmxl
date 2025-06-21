
function test_time() {
    for (let f1 = 10; f1; f1--) {
        f1d = "北京时间：";
        f1d += shell("date '+%Y-%m-%d %H:%M:%S'").result.replace("\n", "");
        f1d += `，程序在${f1}秒后接入人工智能DeepSeek会话。`;
        print(f1d);
        send_mseeage(f1d);
        sleep(1000);

    }
}

function 汽水广告() {
    device.keepScreenOn();
    while (true) {
        text("领取奖励").exists() && click(text("领取奖励").findOne(1).bounds());
        text("继续观看").exists() && click(text("继续观看").findOne(1).bounds());
        text("取消").exists() && click(text("取消").findOne(1).bounds());
        data_str = text("反馈").findOne(1).bounds().centerX();
        sleep(1000);
        if (data_str != text("反馈").findOne(1).bounds().centerX()) {
            data = text("反馈").findOne(1).bounds();
            click(data.centerX() * 1.5, data.centerY());
        }
    }
}

// 使用AutoXJS的http模块发送POST请求
function deepseek(uri, str) {
    let response = http.postJson(
        `http://${uri}:11434/api/generate`, // Ollama的API地址
        {
            "model": "deepseek-r1:7b", // 指定模型
            "prompt": `${str}`, // 提示文本
            "stream": false
        },
        {
            "headers": {
                "Content-Type": "application/json" // 设置请求头
            }
        }
    );
    return response.body.json().response;
}

function send_mseeage(data_str) {
    text("说点什么...").exists() && text("说点什么...").click();
    text("发送消息").exists() && text("发送消息").click();
    sleep(0X20);
    setText(0, data_str);
    text("发送").exists() && text("发送").click();
    desc("发送").exists() && desc("发送").click();
}

function test_send(username) {
    data_str = [];
    for (let f1 of className("TextView").find()) {
        f1 = f1.text();
        if (f1.includes("‎")) {
            for (let f2 of ["‎", "  ", "*"]) while (f1.includes(f2)) f1 = f1.replace(f2, "");
            data_str.push(f1);
        }
    }
    data_str = data_str[data_str.length - 1];
    print(data_str.includes(username))
    if (true || data_str.includes(`${username}`)) {
        print(`输入内容：${data_str}`);
        if (data_str.includes(`来了`))
            data_str = "把来了两个字改成欢迎，欢迎后面要有标点：\n " + data_str;
        else
            data_str = "认真思考后回答，不能超过50字。以下是内容：\n " + data_str;
        data_str = deepseek("192.168.0.155", data_str).split("</think>\n\n")[1];
        if (data_str) send_mseeage(data_str + "（会话由DeepSeek回答）");
        print(`输出内容：${data_str}`);
    }
}

device.keepScreenOn();
print("正在执行人工智能对话。");
if (0) {
    data_str = className("TextView").find()
    data_str = data_str[data_str.length - 2];
    data_str = data_str.text();
    data_str += " 北京时间：";
    data_str += shell("date '+%Y-%m-%d %H:%M:%S'").result.replace("\n", "");
    print(data_str)
    send_mseeage(data_str);
}
else
    test_send("@奶元清宝宝");


