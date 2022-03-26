<script>
    export let baseURL;
    import BookInfoLinks from "../components/BookInfoLinks.svelte";
    import About from "../components/About.svelte";
</script>

<section class="section">
    <div class="container">
        <div class="columns">
            <div class="column is-narrow has-text-centered">
                <img
                    src="/images/SanicCoverFinal.png"
                    alt="Python Web Development with Sanic"
                    style="max-height: 500px;"
                />
            </div>
            <div
                class="column is-flex is-flex-direction-column is-justify-content-center"
            >
                <h2 class="title">
                    Level up your Python and web development skills
                </h2>

                <div class="is-size-3 mt-5">
                    with
                    <a href="https://amhopkins.com">Adam Hopkins</a>, one of the
                    core developers of <em>Sanic</em>
                </div>
            </div>
        </div>
    </div>
</section>

<BookInfoLinks />
<About {baseURL} />

<style>
    em {
        font-style: normal;
        color: #ff0d68;
    }
    a {
        text-decoration: underline;
        color: #ff0d68;
    }
    a:hover {
        text-decoration: none;
        color: #ff0d68;
    }
</style>
