<script>
  import { user } from "$lib/stores/token";
  import {page} from "$app/stores"
</script>

<nav class="bg-base-100 border-b border-base-200 text-white px-4 py-2 flex items-center justify-between">
  <div class="flex items-center gap-4">
    {#if $page.url.pathname !== "/"}
      <button class="btn btn-sm btn-circle btn-ghost" on:click={() => history.back()}><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
</svg></button>
{:else}
  <span class="w-8 block"></span>
    {/if}
  <a href="/" class="text-lg font-bold">Concert</a>
  </div>

  <div class="flex items-center gap-4">
    {#if !$user}
    <a href="/auth" class="btn btn-primary btn-sm px-4 rounded text-white">Sign In</a>
    {:else}
    <a href="/new" class="btn btn-primary btn-sm px-4 rounded text-white">Create stage</a>
    {/if}
  <span class="w-8 block"></span>
  </div>
</nav>
