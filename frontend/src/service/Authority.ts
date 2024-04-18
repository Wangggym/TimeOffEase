import cookie from "js-cookie";

export class Authority {
  static LOGIN_TOKEN = "LOGIN_TOKEN";

  static get() {
    return cookie.get(this.LOGIN_TOKEN);
  }

  static set(token: string) {
    return cookie.set(this.LOGIN_TOKEN, token);
  }

  static clean() {
    cookie.remove(this.LOGIN_TOKEN);
  }
}
