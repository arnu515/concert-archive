<script lang="ts">
  import {page} from "$app/stores"
</script>

<svelte:head>
  <title>An error occured ({$page.status})</title>
</svelte:head>

<div class="grid place-items-center fixed w-full h-full top-0 left-0">
  <div class="rounded-xl text-center bg-base-300 border-2 border-error px-6 py-4">
    <h1 class="my-4 text-4xl font-bold">An error occured ({$page.status})</h1>
    <p class="my-4 text-2xl font-medium font-mono">{$page.error?.message || "An unknown error occured"}</p>
    <p class="flex items-center justify-center my-4 gap-2"><button class="btn btn-accent" on:click={() => history.back()}>Go back</button> <a class="btn btn-primary" href="/">Go home</a></p>
  </div>
</div>
