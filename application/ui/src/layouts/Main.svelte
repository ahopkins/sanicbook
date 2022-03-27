<script>
    export let baseURL;
    import { currentUser } from "../stores/user";
    import Library from "./Library.svelte";
    import BookInfo from "./BookInfo.svelte";
</script>

{#if $currentUser.me}
    <section class="section">
        <div class="container">
            <Library {baseURL} />
        </div>
    </section>
    <section class="section has-background-black-ter">
        <div class="container">
            <div class="columns is-centered">
                <div class="column is-two-thirds-tablet is-half-desktop">
                    <p>
                        The above <strong>My Library</strong> is a playground for
                        you to interact with. You are invited to review the source
                        code for Chapter 11 while playing with this application.
                        You should also try interacting with the API directly.
                    </p>
                    <p>
                        As always, if you have questions ping me on Twitter or
                        on the Sanic Discord server.
                    </p>
                </div>
            </div>
        </div>
    </section>
{/if}
<BookInfo {baseURL} />
