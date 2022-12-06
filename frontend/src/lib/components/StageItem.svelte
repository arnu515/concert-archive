<script lang="ts">
  import type {Stage} from "$lib/util/types"
  import {user} from "$lib/stores/token"

  export let stage: Stage
</script>

<a href="/stages/{stage.id}" class="bg-base-300 border-2 rounded-xl px-6 py-3 flex flex-col justify-center cursor-pointer gap-2" style="border-color: {stage.color}">
  <h3 class="text-2xl font-medium flex items-center justify-between" style="color: {stage.color}">{stage.name}
  <span class="text-gray-500 text-sm">{stage.id}</span>
  </h3>
  <div class="text-lg flex items-center justify-between">
    <p class="flex items-center gap-2"><img src="{stage.owner.avatar_url}" class="w-8 h-8 rounded-full border border-white" alt="{stage.owner.id}'s avatar"> {stage.owner.id}</p>
  <div class="flex items-center gap-2">
    {#if stage.owner_id === $user?.id}
    <span class="badge badge-warning">Your stage</span>
    {/if}
    {#if stage.private}
    <span class="badge badge-accent uppercase">Private</span>
    {/if}
  </div>
</div>
</a>
