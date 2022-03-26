<script>
    export let authCode;
    export let baseURL;

    import { onMount } from "svelte";
    import { getCookie } from "../utils/cookie";
    import { me } from "../utils/account";
    import { currentUser } from "../stores/user";

    const getUser = me(baseURL, getCookie("access_token"));
</script>

<nav class="navbar" role="navigation" aria-label="main navigation">
    <div class="navbar-brand">
        <a class="navbar-item" href={baseURL}>
            <img
                src="https://raw.githubusercontent.com/huge-success/sanic-assets/master/png/sanic-framework-logo-simple-white-400x97.png"
                width="112"
                height="28"
                alt="Sanic Framework"
            />
        </a>
    </div>

    <div id="navbarBasicExample" class="navbar-menu">
        <div class="navbar-start">
            <a
                href="https://github.com/PacktPublishing/Web-Development-with-Sanic"
                class="navbar-item"
            >
                Source Code
            </a>

            <div class="navbar-item has-dropdown is-hoverable">
                <a href="http://" class="navbar-link"> More </a>

                <div class="navbar-dropdown">
                    <a
                        href="https://sanic.dev/en/help.html"
                        class="navbar-item"
                    >
                        Sanic Help
                    </a>
                    <a href="https://sanic.dev/en/" class="navbar-item">
                        Sanic User Guide
                    </a>
                    <hr class="navbar-divider" />
                    <a href="https://twitter.com/AdmHpkns" class="navbar-item">
                        Twitter: @admhpkns
                    </a>
                    <a href="https://github.com/ahopkins" class="navbar-item">
                        Github: /ahopkins
                    </a>
                    <a
                        href="https://github.com/ahopkins/sanicbook"
                        class="navbar-item"
                    >
                        Actual deployed source
                    </a>
                </div>
            </div>
        </div>

        <div class="navbar-end">
            <div class="navbar-item">
                <div class="buttons">
                    <a href="http://" class="button is-link">
                        <strong>Buy the book</strong>
                        <span class="icon is-small">
                            <i class="fas fa-book" />
                        </span>
                    </a>
                    {#await getUser}
                        <a
                            href={`${baseURL}/api/v1/auth/github`}
                            class="button is-light"
                            disabled
                        >
                            <span>Loading</span>
                            <span class="icon is-small">
                                <i class="fas fa-circle-notch fa-spin" />
                            </span>
                        </a>
                    {:then}
                        {#if $currentUser.me}
                            <a
                                href={$currentUser.me.profile}
                                class="button"
                                target="_blank"
                            >
                                <span>{$currentUser.me.login}</span>
                                <span class="icon avatar-wrapper">
                                    <img
                                        src={$currentUser.me.avatar}
                                        alt={$currentUser.me.name}
                                        class="avatar"
                                    />
                                </span>
                            </a>
                        {:else}
                            <a
                                href={`${baseURL}/api/v1/auth/github`}
                                class="button is-light"
                                disabled={authCode}
                            >
                                <span>Login with Github</span>
                                <span class="icon is-small">
                                    <i class="fab fa-github" />
                                </span>
                            </a>
                        {/if}
                    {/await}
                </div>
            </div>
        </div>
    </div>
</nav>

<style>
    nav {
        border-width: 0;
    }
    .avatar {
        width: 28px;
        height: 28px;
        border-radius: 100%;
    }
</style>
