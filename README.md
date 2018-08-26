Implementation example of LINE Pay without SDK.
If you want to use Node.js & SDK, please refer to [nkjm/line-pay](https://github.com/nkjm/line-pay).

# Usage

* Register sandbox at https://pay.line.me/jp/developers/techsupport/sandbox/creation?locale=ja_JP.
* Login information E-mail will be sent. Login.
* Get credential at https://pay.line.me/center/notice/list.
* Replace credentials in `app.js` with yours.
* Launch this project. `python app.js`
* Install ngrok and tunnel to local. `ngrok http 5000`
* Access with web browser `https://xxxxxxxx.ngrok.io`
