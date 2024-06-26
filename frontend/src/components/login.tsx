/**
 * This code was generated by v0 by Vercel.
 * @see https://v0.dev/t/dPYpSxxopnW
 */
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Authority } from "@/service/Authority";
import request from "@/service/WebClient";
import { get } from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { ChangeEventHandler, useState } from "react";

export function Login() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleChangeEmail: ChangeEventHandler<HTMLInputElement> = (e) => {
    setEmail(e.target.value);
  };

  const handleChangePassword: ChangeEventHandler<HTMLInputElement> = (e) => {
    setPassword(e.target.value);
  };

  const handleClickSubmit = async () => {
    const result = await request("/api/login", {
      method: "post",
      data: {
        email,
        password,
      },
    });
    const accessToken = get(result, "access_token");
    if (accessToken) {
      Authority.set(accessToken);
      router.push("/");
    }
  };

  return (
    <div className="flex items-center min-h-screen px-6">
      <div className="w-full max-w-md space-y-4 mx-auto">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">Login</h1>
          <p className="text-gray-500 dark:text-gray-400">
            Enter your email below to login to your account
          </p>
        </div>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              placeholder="m@example.com"
              required
              type="email"
              value={email}
              onChange={handleChangeEmail}
            />
          </div>
          <div className="space-y-2">
            <div className="flex items-center">
              <Label htmlFor="password">Password</Label>
              {/* <Link className="ml-auto inline-block text-sm underline" href="#">
                Forgot your password?
              </Link> */}
            </div>
            <Input
              id="password"
              required
              type="password"
              value={password}
              onChange={handleChangePassword}
            />
          </div>
          <Button className="w-full" onClick={handleClickSubmit}>
            Login
          </Button>
          {/* <Button className="w-full" variant="outline">
            Login with Google
          </Button> */}
        </div>
        <div className="mt-4 text-center text-sm">
          {/* eslint-disable-next-line */}
          Don't have an account?
          <Link className="underline" href="/signup">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
