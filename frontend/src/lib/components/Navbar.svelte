<script>
  import { user } from "$lib/stores/token";
</script>

<nav class="bg-base-100 border-b border-base-200 text-white px-4 py-2 flex items-center justify-between">
  <a href="/" class="text-lg font-bold">Concert</a>

  <div class="flex items-center gap-4">
    {#if !$user}
    <a href="/auth" class="btn btn-primary btn-sm px-4 rounded text-white">Sign In</a>
    {:else}
    <a href="/new" class="btn btn-primary btn-sm px-4 rounded text-white">Create stage</a>
    {/if}
  </div>
</nav>
