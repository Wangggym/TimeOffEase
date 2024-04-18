import { Dashboard } from "@/components/dashboard";
import request from "@/service/WebClient";
import React, { useEffect } from "react";

const Home: React.FC = () => {
  
  const fetchMe = async () => {
    await request("/api/me", {
      method: "get",
    });
  };

  useEffect(() => {
    fetchMe()
  }, []);

  return (
    <div>
      <Dashboard />
    </div>
  );
};

export default Home;
