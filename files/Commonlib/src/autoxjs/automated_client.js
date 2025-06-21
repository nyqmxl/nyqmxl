function _open_(_res_, _ws_, _data_) {
    let _verify_ = http.get(
        `${_data_.config.uri_code}/${_data_.message.secret}`, {
        timeout: 5000
    });
    if (_verify_.statusCode === 200) {
        _verify_ = _verify_.body.json()
        _data_.message.code = _verify_.code
        _verify_ = JSON.stringify(_data_.message, null, 4);
        _ws_.send(_verify_);
        print(`\nWebSocket连接已建立，以下是服务器和验证信息：\n${_data_.config.uri_ws}\n${_verify_}\n`);
        _ws_.re
    }
    else
        _ws_.close();
}

function _message_(_text_, _ws_, _data_) {
    try {
        print("receive:", _text_);
        _text_ = JSON.parse(_text_);
        if (_text_.data) {
            _text_.device = _data_.message.device
            _text_.type = _data_.message.type
            _text_.data = {
                "status": true,
                "code": _text_.data,
                "return": ""
            };
            try {
                _text_.data.return = eval(_text_.data.code);
            } catch (error) {
                _text_.data.status = false;
                _text_.data.return = error.toString();
            }
            print(_text_.data)
            _text_ = JSON.stringify(_text_, null, 4);
            print("send:", _text_)
            _ws_.send(_text_);
        }
    }
    catch (error) {
        _text_ = {
            "error": error.toString(),
            "text": _text_
        }
        print(JSON.stringify(_text_, null, 4))
    }
}

function _error_(_err_, _ws_) {
    console.error("\nWebSocket连接失败，尝试重新连接");
    return true;
}

function _close_(_code_, _reason_, _ws_) {
    console.error("\nWebSocket连接关闭，尝试重新连接");
    return true;
}

function _websocket_(_data_) {
    setInterval(() => {
        if (_data_.config.reconnect)
            try {
                _data_.config.reconnect = false;
                let _ws_ = web.newWebSocket(_data_.config.uri_ws, { eventThread: 'this' });
                _ws_.on("open", _event_ => _open_(_event_, _ws_, _data_))
                    .on("text", _msg_ => _message_(_msg_, _ws_, _data_))
                    .on("failure", (_err_, _res_, _ws_) => { _data_.config.reconnect = _error_(_err_, _ws_); })
                    .on("closing", (_code_, _reason_, _ws_) => { _data_.config.reconnect = _close_(_code_, _reason_, _ws_); });
            }
            catch (error) { _data_.config.reconnect = true; log(error) }

    }, _data_.config.timeout);
}

function main(path) {
    let _data_ = {
        "config": {
            "uri_ws": "ws://206.119.166.200:8500",
            "uri_code": "http://206.119.166.200:8502/code",
            "running": true,
            "reconnect": true,
            "timeout": 5000,
        },
        "message": {
            "secret": device.getAndroidId(),
            "code": "",
            "device": device.getAndroidId(),
            "type": "default.apk"
        }
    };
    try {
        _data_ = JSON.parse(files.read(path))
    }
    catch (error) {
        files.write(path, JSON.stringify(_data_, null, 4));
    }
    if (_data_.config.running) _websocket_(_data_);
    return null;
}

print("配置文件存放于：文件根目录！")
main("/storage/emulated/0/auto_config.json");
