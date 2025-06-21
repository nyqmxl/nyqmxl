function click_element(pointer) {
    return click(pointer.bounds());
}

function unlock_screen() {
    device.wakeUp();
    swipe(
        parseInt(device.width * 0.5),
        parseInt(device.height * 0.8),
        parseInt(device.width * 0.5),
        parseInt(device.height * 0.2),
        500
    );
    device.keepScreenOn();
}

function edge_setting(app_name, app_download_url, target_url) {
    if (app.launch(app_name)) {
        sleep(10 * 1000);
        if (!desc("浏览器菜单").exists()) {
            const menu_items = ["Edge", "设为默认浏览器", "Edge", "设为默认应用", "以后再说", "确认"];
            for (let menu_item of menu_items) {
                while (!text(menu_item).exists()) sleep(500);
                if (text(menu_item).exists()) click_element(text(menu_item).findOne(1));
            }
        }
        sleep(1 * 1000);
        if (desc("浏览器菜单").exists()) {
            const setting_flow = [
                "浏览器菜单",
                "设置",
                "常规",
                "网站显示设置",
                "将桌面站点显示为默认值",
                "ImageButton",
                "启动时",
                "特定页",
                "输入 Web 地址",
                "保存",
                "ImageButton",
                "ImageButton",
                "浏览器菜单",
                "主页",
            ];

            for (let item of setting_flow) {
                do {
                    sleep(1000);
                } while (!desc(item).exists() && !text(item).exists() && !className("ImageButton").exists());

                switch (item) {
                    case "浏览器菜单":
                        if (desc(item).exists()) desc(item).click();
                        break;
                    case "启动时":
                        swipe(
                            parseInt(device.width * 0.5),
                            parseInt(device.height * 0.8),
                            parseInt(device.width * 0.5),
                            parseInt(device.height * 0.2),
                            10
                        );
                        break;
                    case "输入 Web 地址":
                        text(item).setText(target_url);
                        break;
                    case "保存":
                        text(item).click();
                        break;
                    case "ImageButton":
                        className(item).click();
                        break;
                    default:
                        if (text(item).exists()) click_element(text(item).findOne(1));
                }
            }
        }
        toast("配置 Edge浏览器 成功！");
        return true;
    } else {
        app.openUrl(app_download_url);
        toast("请根据提示下载并安装 “Edge” 浏览器。\n配置 Edge浏览器 失败！！！");
        return false;
    }
}

function tiktok_welcome() {
    sleep(5 * 1000);
    swipe(
        parseInt(device.width * 0.5),
        parseInt(device.height * 0.8),
        parseInt(device.width * 0.5),
        parseInt(device.height * 0.2),
        500
    );
    const buttons = ["跳过", "开始观看", "同意并继续", "确定"];
    for (let button of buttons) text(button).click();
    sleep(10 * 1000);
    className("android.widget.ImageView").find()[1].click();
    while (!text("上滑查看更多视频").exists()) sleep(200);
    swipe(
        parseInt(device.width * 0.5),
        parseInt(device.height * 0.8),
        parseInt(device.width * 0.5),
        parseInt(device.height * 0.2),
        500
    );
}

function tiktok_register() {
    if (text("创建账号").exists()) {
        text("创建账号").click();
        className("android.widget.EditText").setText("user_111119192233_001");
        sleep(5 * 1000);
        click_element(text("下一步").findOne());
        sleep(1 * 1000);
        className("android.widget.EditText").setText("admin@12345");
        sleep(1 * 1000);
        click_element(text("下一步").findOne());
    } else {
        if (className("TextView").findOne(1).text() == "登录 TikTok") text("还没有账号？注册").click(), sleep(1000);
        const registration_steps = ["使用手机或电子邮件", "生日", "下一步", "电子邮件", "电子邮件", "电子邮件地址", "继续"];

        for (let step of registration_steps) {
            switch (step) {
                case "生日":
                    do {
                        sleep(500);
                    } while (!(className("android.widget.EditText").findOne(1).text() == step));
                    print("测试");
                    const selectors = ["年份选择器", "月份选择器", "日期选择器"];
                    for (let selector of selectors) {
                        let bounds = desc(selector).findOne(1).bounds();
                        swipe(
                            bounds.centerX(),
                            bounds.centerY(),
                            bounds.centerX(),
                            device.height,
                            Math.floor(Math.random() * 45 + 50)
                        );
                    }
                    sleep(3 * 1000);
                    let birthday_text = className("android.widget.EditText").findOne(1).text();
                    print(birthday_text);
                    break;
                case "电子邮件地址":
                    while (!text(step).exists()) sleep(100);
                    text(step).setText("测试");
                    break;
                default:
                    while (!text(step).exists()) sleep(100);
                    click_element(text(step).findOne(1));
            }
        }
    }
}

function tiktok_login() {
    if (className("TextView").findOne(1).text() == "注册 TikTok") text("已有账号？登录").click();
    const login_steps = ["使用手机 / 邮箱 / 用户名", "邮箱/用户名", "电子邮件或用户名", "继续", "验证码"];
    for (let step of login_steps) {
        print(step);
        switch (step) {
            case "电子邮件或用户名":
                if (className("android.widget.EditText").text(step).exists())
                    className("android.widget.EditText").text(step).setText("AadenAbrial@outlook.com");
                break;
            case "验证码":
                if (className("android.widget.EditText").exists()) className("android.widget.EditText").findOne(1).setText(408444);
                break;
            case "继续":
                if (className("android.widget.Button").exists()) className("android.widget.Button").find()[4].click();
                break;
            default:
                if (text(step).exists()) click_element(text(step).findOne(1));
                sleep(1000);
        }
    }
}

function tiktok_qrcode(login_qr_uri) {
    if (!login_qr_uri.length) return null;
    login_qr_uri = login_qr_uri[0];
    toast("正在唤醒 TikTok 应用授权。");
    app.startActivity({ data: `snssdk1180://webview?url=${login_qr_uri}&from=webview&refer=web` });
    while (!text("确认").exists()) sleep(500);
    sleep(2 * 1000);
    text("确认").click();
    toast("应用 TikTok 授权成功。");
    sleep(3 * 1000);
    back();
    if (text("确认").exists()) return false;
    return true;
}

function test_activity(uri) {
    app.startActivity({ data: `snssdk1180://webview?url=${uri}&from=webview&refer=web` });
    return true;
}

// edge_setting("com.microsoft.emmx", "https://www.baidu.com", "https://www.tiktok.com/login/qrcode");
// css-1fwlm1o-DivPanelContainer ea3pfar1