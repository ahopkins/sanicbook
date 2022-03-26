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
{:else}
    <BookInfo {baseURL} />
{/if}
