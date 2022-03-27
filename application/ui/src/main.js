import App from "./App.svelte";

const app = new App({
    target: document.body,
    // props: { baseURL: "http://localhost:7777" },
    props: { baseURL: "https://sanicbook.herokuapp.com" },
});

export default app;
