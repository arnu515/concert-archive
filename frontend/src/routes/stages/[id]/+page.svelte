<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount, onDestroy } from "svelte"
  import {user, token} from "$lib/stores/token"
  import type { PageData } from "./$types";
  import { currentStage, stageToken, stageRoom , stageReconnecting, leaveStage, connectToStage, stageCanSpeak, chatMessages, stageSpeakers} from "$lib/stores/stage";
  import { addToasts } from "$lib/stores/toasts";
  import type {Stage} from "$lib/util/types"
  import { fetch } from "$lib/util/fetch";
  import LoadingSpinner from "$lib/components/LoadingSpinner.svelte";
  import Participant from "$lib/components/Participant.svelte";


  export let data: PageData;
  const stage = data.stage as Stage;
  $currentStage = {...stage}
  let hasRequestedToSpeak = false;
  let requestToSpeakTimeout: NodeJS.Timeout | null = null;
  let typedMessage = ""
  let isSendingChatMessage = false
  let messagesBox: HTMLDivElement| undefined
  let isTogglingSpeaker = false

  onMount(async () => {
    if (!$user) return goto("/auth?next=" + encodeURIComponent(window.location.pathname))
    console.info("Joining stage")
    console.log($stageRoom, $stageToken, $currentStage)
    if ($stageRoom) {
      console.info("Already connected to a stage")
      return
    }

    const res = await fetch(`/api/stage/${stage.id}/token`, {headers: {Authorization: "Bearer " + $token}})
    const data = await res.json()
    if (!res.ok) {
      console.error(res.status,"Could not join stage", data)
    addToasts([{title: "Could not join stage", class: "alert-error", message: "You could not join the stage. Press F12 for details."}])
    $currentStage = null;
    return
    }

    $stageToken = data.token
    await connectToStage($stageToken!, () => {
      addToasts([{title: "Disconnected", class: "alert-warning", message: "You were disconnected from the stage."}])
    })

    return () => {
      if(requestToSpeakTimeout) clearTimeout(requestToSpeakTimeout)
    }
  });

  async function requestToSpeak() {
    if (!$stageRoom) return
    if ($stageCanSpeak) {
      addToasts([{title: "Failed", class: "alert-warning", message: "You already have permission to speak on this stage."}])
      return
    }
    if (hasRequestedToSpeak) {
      addToasts([{title: "Failed", class: "alert-warning", message: "You have already requested to speak on this stage. Please wait a bit before doing it again"}])
      return
    }

    hasRequestedToSpeak = true
    requestToSpeakTimeout= setTimeout(() => hasRequestedToSpeak = false, 300000)

    const res= await fetch(`/api/stage/${stage.id}/request_to_speak`, {method: "POST", headers: {Authorization: "Bearer " + $token, "X-Livekit-Token": $stageToken!}})
    if (!res.ok) {
      const data = await res.json()
      console.error(res.status, "Failed to request to speak", data)
      addToasts([{title: "Failed", class: "alert-warning", message: "Failed to request to speak. Press F12 for details."}])
    }
  }

  async function sendMessage() {
    if (isSendingChatMessage) return
    if (!typedMessage.trim()) return
    isSendingChatMessage = true
    const res = await fetch(`/api/stage/${stage.id}/chat`, {method: "POST", headers: {Authorization: "Bearer " + $token, "X-Livekit-Token": $stageToken!, "Content-Type": "application/json"}, body: JSON.stringify({message: typedMessage.trim()})})
    isSendingChatMessage = false
    if (!res.ok) {
      const data = await res.json()
      console.error(res.status, "Failed to send message", data)
      addToasts([{title: "Failed", class: "alert-warning", message: "Failed to send message. Press F12 for details."}])
    }

    typedMessage = ""
  }

  async function toggleSpeaker(p: {identity: string}, toggle: boolean) {
    if (isTogglingSpeaker) return;
    isTogglingSpeaker =true;
    const res = await fetch(`/api/stage/${stage.id}/owner/make_${toggle ? "speaker" : "listener"}`, {method: "POST", headers: {Authorization: "Bearer " + $token, "X-Livekit-Token": $stageToken!, "Content-Type": "application/json"}, body: JSON.stringify({user_id: p.identity})})
    isTogglingSpeaker =false;
    if (!res.ok) {
      const data = await res.json()
      console.error(res.status, "Failed to toggle speaker", data)
      addToasts([{title: "Failed", class: "alert-warning", message: "Failed to toggle speaker. Press F12 for details."}])
    }
  }

  // onDestroy(() => {
  //   console.info("Leaving stage")
  //   leaveStage()
  // })

  // $: if (!$currentStage) {
  //   goto("/")
  // }
    $: console.log({room: $stageRoom, token: $stageToken, stage: $currentStage})

  $: if ($chatMessages) {
    if (messagesBox?.lastChild) {
      (messagesBox.lastChild as HTMLDivElement).scrollIntoView({behavior: "smooth"})
    }
  }
</script>

{#if $stageReconnecting}
<div class="grid place-items-center fixed w-full h-full top-0 left-0">
  <div class="rounded-xl text-center bg-base-300 border-2 border-error px-6 py-4">
    <h1 class="my-4 text-4xl font-bold">Reconnecting to stage</h1>
    <div class="flex items-center justify-center my-4"><LoadingSpinner /></div>
    <div class="flex items-center justify-center my-4">
      <button class="btn btn-error" on:click={() => {
        if (window.confirm("Are you sure?")) leaveStage()
      }}>Disconnect</button>
    </div>
  </div>
</div>
{:else if $stageRoom && $user && $currentStage}
<main>
  <div class="flex flex-col gap-2 rounded-xl bg-base-300 px-6 py-4 border overflow-hidden" style="border-color: {stage.color}">
    <h1 class="text-3xl font-bold mb-4 mt-4 flex items-center gap-4 truncate min-h-[2.5rem]" style="color: {stage.color}"><span class="text-white">Stage:</span> {stage.name}</h1>
    <div class="flex items-center gap-4 overflow-x-auto min-h-[4rem] pb-4">
      {#if $stageCanSpeak}
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
      {:else}
      <button class="btn gap-4 btn-accent" title="Request to speak" aria-label="Request to speak" disabled={hasRequestedToSpeak} on:click={requestToSpeak}>
        {#if true}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
  <path d="M18 8a3 3 0 0 1 0 6" />
  <path d="M10 8v11a1 1 0 0 1 -1 1h-1a1 1 0 0 1 -1 -1v-5" />
  <path d="M12 8h0l4.524 -3.77a0.9 .9 0 0 1 1.476 .692v12.156a0.9 .9 0 0 1 -1.476 .692l-4.524 -3.77h-8a1 1 0 0 1 -1 -1v-4a1 1 0 0 1 1 -1h8" />
</svg> { hasRequestedToSpeak ? "Requested" : "Request to speak"}
{:else}
<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
  <path d="M5 4h6a3 3 0 0 1 3 3v7" />
  <path d="M10 10l4 4l4 -4m-8 5l4 4l4 -4" />
</svg> Become a listener
{/if}
      </button>
      {/if}
      <button class="btn btn-error btn-outline ml-auto" on:click={() => {
        if (window.confirm("Are you sure?")) {
          leaveStage()
          goto("/")
        }
      }}>Exit Stage</button>
    </div>
    <h3 class="text-xl my-6 font-black uppercase">Speakers ({$stageSpeakers.length})</h3>
    <div class="flex gap-6 overflow-x-auto pb-4 min-h-[8rem]">
      {#each Array.from($stageRoom?.participants.values()).filter(i => $stageSpeakers.includes(i.identity)) as p}
      <Participant isOwner={$user.id === stage.owner_id} on:toggleSpeaker={() => toggleSpeaker(p, false)} {p} isSpeaker />
      {/each}
      {#if $stageSpeakers.includes($stageRoom?.localParticipant?.identity)}
      <Participant p={$stageRoom.localParticipant} isSpeaker />
      {/if}
    </div>

    <!-- +1 below to account for localParticipant, which is not there in room.participants -->
    <h3 class="text-xl my-6 font-black uppercase">Listeners ({($stageRoom.participants.size + 1) - $stageSpeakers.length})</h3>
    <div class="flex gap-6 overflow-auto flex-wrap">
      {#each Array.from($stageRoom?.participants.values()).filter(i => !$stageSpeakers.includes(i.identity)) as p}
      <Participant isOwner={$user.id === stage.owner_id} on:toggleSpeaker={() => toggleSpeaker(p, true)} {p} />
      {/each}
      {#if !$stageSpeakers.includes($stageRoom.localParticipant?.identity)}
      <Participant p={$stageRoom.localParticipant} />
      {/if}
    </div>
  </div>
  <div class="flex flex-col gap-2 rounded-xl bg-base-300 px-6 py-4 border overflow-hidden" style="border-color: {stage.color}">
    <h2 class="text-5xl font-bold my-4 flex items-center justify-between" style="color: {stage.color}">Chat</h2>
    <div class="messages flex flex-col gap-8 pr-2 my-2" bind:this={messagesBox}>
      {#each $chatMessages as message}
        {#if message.type === "TEXT"}
      <div class="flex items-center gap-2">
        <img src="{message.user.avatar_url}" alt="{message.user.username}'s avatar" class="w-6 h-6 rounded-full border border-white">
        <span><strong>{message.user.username}</strong>:</span>
        <span>{message.message_data}</span>
      </div>
      {:else if message.type === "FILE"}
      <div class="flex justify-center flex-col gap-2">
        <div class="flex items-center gap-2">
        <img src="{message.user.avatar_url}" alt="{message.user.username}'s avatar" class="w-6 h-6 rounded-full border border-white">
        <span><strong>{message.user.username}</strong> uploaded a file</span>
        </div>
        {#if /.*\.(png|jpeg|gif|webp)/.test(message.message_data)}
        <a href="{message.message_data}" target="_blank" rel="noreferrer" class="flex items-center my-1 w-full">
          <img src={message.message_data} class="rounded w-full" alt="Uploaded by {message.user.username}">
        </a>
        {:else if /.*\.(mp4|webm)/.test(message.message_data)}
        <a href="{message.message_data}" target="_blank" rel="noreferrer" class="flex items-center my-1 w-full">
          <video controls src={message.message_data} class="rounded w-full"/>
        </a>
        {:else if /.*\.(mp3|aac|ogg|flac)/.test(message.message_data)}
        <a href="{message.message_data}" target="_blank" rel="noreferrer" class="flex items-center my-1 w-full">
          <audio controls src={message.message_data} class="rounded w-full"/>
        </a>
        {:else}
        <div class="bg-base-100 items-center rounded-xl my-4 flex px-4 py-2 border border-gray-500"><p class="text-xl font-mono"><span class="badge badge-accent uppercase">{message.message_data.split(".").pop()}</span> {message.message_data.split("/").pop()}</p> <a
href="{message.message_data}" target="_blank" rel="noreferrer" 
           class="btn btn-ghost btn-circle btn-sm ml-auto"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
</svg></a></div>
        {/if}
      </div>
      {:else if message.type === "EVENT"}
      {#if message.message_data === "REQUEST_TO_SPEAK"}
      <div class="flex items-center justify-center gap-2">
        <img src="{message.user.avatar_url}" alt="{message.user.username}'s avatar" class="w-6 h-6 rounded-full border border-white">
        <span><strong>{message.user.username}</strong></span>
        <span class="text-gray-500">wishes to speak</span>
      </div>
      {:else if message.message_data === "MADE_SPEAKER"}
      <div class="flex items-center justify-center gap-2">
        <img src="{message.user.avatar_url}" alt="{message.user.username}'s avatar" class="w-6 h-6 rounded-full border border-white">
        <span><strong>{message.user.username}</strong></span>
        <span class="text-gray-500">is now a speaker</span>
      </div>
      {:else if message.message_data === "MADE_LISTENER"}
      <div class="flex items-center justify-center gap-2">
        <img src="{message.user.avatar_url}" alt="{message.user.username}'s avatar" class="w-6 h-6 rounded-full border border-white">
        <span><strong>{message.user.username}</strong></span>
        <span class="text-gray-500">is now a listener</span>
      </div>
        {/if}
        {/if}
      {/each}
      <div class="my-2"></div>
    </div>
    <input disabled={isSendingChatMessage} readonly={isSendingChatMessage} type="text" class="input w-full m-1 mt-auto" placeholder="Type message and press enter" aria-label="Message" bind:value={typedMessage} on:keypress={(e) => {
      if (e.key.toLowerCase() === "enter" && !!typedMessage.trim()) {
        sendMessage()
      }
    }}>
  </div>
  </main>
  {:else}
  <div class="flex items-center justify-center mt-20"><LoadingSpinner /></div>
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
