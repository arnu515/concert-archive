<script lang="ts">
  import type { Participant } from "livekit-client";
  import {user} from "$lib/stores/token"
  import {createEventDispatcher} from "svelte"

  export let p: Participant
  export let isSpeaker = false
  export let isOwner = false
  const m = JSON.parse(p.metadata || "{}")
  const isMe = $user?.id === p.identity
  const d = createEventDispatcher()

  function toggleSpeaker() {
    if (!isOwner || isMe) return
    if (!window.confirm("Are you sure you want to make " + p.name + " a " + (isSpeaker ? "listener" : "speaker") + "?")) return
    d("toggleSpeaker")
  }
</script>

<div class="flex flex-col gap-3 items-center justify-center {isOwner && !isMe ? "hover:brightness-90 transition-all cursor-pointer" : ""}" role={isOwner &&!isMe ? "button" : undefined} on:click={isOwner &&!isMe ? toggleSpeaker: undefined} title={isOwner &&!isMe ? isSpeaker ? "Make listener" : "Make speaker" : undefined}>
  <img src="{m.avatar_url}" alt="avatar" class="w-20 h-20 rounded-full border border-white">
  <p class="text-center font-bold truncate font-mono" class:badge={isSpeaker} style={isSpeaker? `background-color: ${m.color}; border-color: currentColor; color: white`: `color: ${m.color}`}>{isMe ? "You" : m.username}</p>
</div>
