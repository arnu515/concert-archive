<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte"
  import {user} from "$lib/stores/token"
  import type { PageData } from "./$types";
  import { currentStage } from "$lib/stores/stage";

  export let data: PageData;
  $currentStage = {...data.stage}
  let isJoined =true

  onMount(() => {
    if (!$user) return goto("/")
  });
</script>

{#if isJoined}
<main>
  <div class="flex flex-col gap-2 rounded-xl bg-base-300 px-6 py-4 border overflow-hidden" style="border-color: {data.stage.color}">
    <h1 class="text-3xl font-bold mb-4 mt-4 flex items-center gap-4 truncate min-h-[2.5rem]" style="color: {data.stage.color}"><span class="text-white">Stage:</span> {data.stage.name}</h1>
    <div class="flex items-center gap-4 overflow-x-auto min-h-[4rem] pb-4">
      <button class="btn gap-4 btn-primary text-white">
        {#if true}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
  <rect x="9" y="2" width="6" height="11" rx="3" />
  <path d="M5 10a7 7 0 0 0 14 0" />
  <line x1="8" y1="21" x2="16" y2="21" />
  <line x1="12" y1="17" x2="12" y2="21" />
</svg> Unmute
        {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
  <line x1="3" y1="3" x2="21" y2="21" />
  <path d="M9 5a3 3 0 0 1 6 0v5a3 3 0 0 1 -.13 .874m-2 2a3 3 0 0 1 -3.87 -2.872v-1" />
  <path d="M5 10a7 7 0 0 0 10.846 5.85m2.002 -2a6.967 6.967 0 0 0 1.152 -3.85" />
  <line x1="8" y1="21" x2="16" y2="21" />
  <line x1="12" y1="17" x2="12" y2="21" />
</svg> Mute
        {/if}
      </button>
      <button class="btn gap-4 btn-accent" title="Request to speak" aria-label="Request to speak">
        {#if true}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
  <path d="M18 8a3 3 0 0 1 0 6" />
  <path d="M10 8v11a1 1 0 0 1 -1 1h-1a1 1 0 0 1 -1 -1v-5" />
  <path d="M12 8h0l4.524 -3.77a0.9 .9 0 0 1 1.476 .692v12.156a0.9 .9 0 0 1 -1.476 .692l-4.524 -3.77h-8a1 1 0 0 1 -1 -1v-4a1 1 0 0 1 1 -1h8" />
</svg> Request to speak
{:else}
<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
  <path d="M5 4h6a3 3 0 0 1 3 3v7" />
  <path d="M10 10l4 4l4 -4m-8 5l4 4l4 -4" />
</svg> Become a listener
{/if}
      </button>
      <button class="btn btn-error btn-outline ml-auto">Exit Stage</button>
    </div>
    <h3 class="text-xl my-6 font-black uppercase">Speakers (10)</h3>
    <div class="flex gap-6 overflow-x-auto pb-4 min-h-[8rem]">
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
    </div>

    <h3 class="text-xl my-6 font-black uppercase">Listeners (10)</h3>
    <div class="flex gap-6 overflow-auto flex-wrap">
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
      <div class="flex flex-col gap-3 items-center justify-center">
        <img src="{data.stage.owner.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
        <p class="text-center font-bold truncate font-mono">{data.stage.owner.username}</p>
      </div>
    </div>
  </div>
  <div class="flex flex-col gap-2 rounded-xl bg-base-300 px-6 py-4 border overflow-hidden" style="border-color: {data.stage.color}">
    <h2 class="text-5xl font-bold my-4 flex items-center justify-between" style="color: {data.stage.color}">Chat</h2>
    <div class="messages flex flex-col gap-8 pr-2">
      <div class="flex items-center gap-2">
        <img src="{data.stage.owner.avatar_url}" alt="{data.stage.owner.username}'s avatar" class="w-6 h-6 rounded-full border border-white">
        <span><strong>{data.stage.owner.username}</strong>:</span>
        <span>this is a test message</span>
      </div>
      <div class="flex justify-center flex-col gap-2">
        <div class="flex items-center gap-2">
        <img src="{data.stage.owner.avatar_url}" alt="{data.stage.owner.username}'s avatar" class="w-6 h-6 rounded-full border border-white">
        <span><strong>{data.stage.owner.username}</strong> uploaded a file</span>
        </div>
        <img src="https://picsum.photos/1280/720" class="rounded w-full" alt="Uploaded by {data.stage.owner.username}">
      </div>
      <div class="flex justify-center flex-col gap-2">
        <div class="flex items-center gap-2">
        <img src="{data.stage.owner.avatar_url}" alt="{data.stage.owner.username}'s avatar" class="w-6 h-6 rounded-full border border-white">
        <span><strong>{data.stage.owner.username}</strong> uploaded a file</span>
        </div>
        <div class="bg-base-100 items-center rounded-xl my-4 flex px-4 py-2 border border-gray-500"><p class="text-xl font-mono"><span class="badge badge-accent">PDF</span> asdfasdf...sad.pdf</p> <button class="btn btn-ghost btn-circle btn-sm ml-auto"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
</svg></button></div>
      </div>
    </div>
    <input type="text" class="input w-full m-1 mt-auto" placeholder="Type message and press enter" aria-label="Message">
  </div>
  </main>
{/if}

<style lang="postcss">
  main {
    @apply px-2 md:px-4 max-h-[1000px];
    display: grid;
    gap: 1rem;
  }

  .messages {
    @apply overflow-auto my-4;
    scrollbar-width: thin;
    scrollbar-color: theme(colors.primary) theme(colors.base-300);
  }
  .messages::-webkit-scrollbar {
    width: 2px;
    background-color: theme(colors.base-300);
  }
  .messages::-webkit-scrollbar-thumb {
    width: 2px;
    background-color: theme(colors.primary);
  }

  @screen sm {
    main {
      margin: 1rem 2rem;
      grid-template-columns: 1fr;
      grid-template-rows: 3fr 1fr;
    }
  }
  @screen md {
    main {
      margin: 2rem 4rem;
      height: 90vh;
      grid-template-columns: 3fr 1fr;
      grid-template-rows: 1fr;
    }
  }
</style>
