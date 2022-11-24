<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import {user} from "$lib/stores/token"

  let selectedColor = '#00A9A5'
  let createStageBtn: HTMLButtonElement

  onMount(() => {
		if (!$user) {
			goto("/auth")
      return
		}
  });

  function generateRandomColor() {
    const randomColor = Math.floor(Math.random()*16777215).toString(16);
    selectedColor = `#${randomColor}`
  }

  $: if (createStageBtn) {
    createStageBtn.style.backgroundColor = selectedColor
  }
</script>

{#if $user}
  <div class="text-center text-5xl mt-20 font-bold">Create a stage</div>
<form class="card max-w-[400px] min-w-[200px] w-[50%]">
    <div class="my-2">
      <label for="name" class="label">
        <span class="label-text">Stage name</span>
      </label>
      <input type="text" id="name" placeholder="Enter a name for your stage" name="name" required autocomplete="off" class="input w-full">
    </div>
    <div class="my-2">
      <label for="password" class="label">
        <span class="label-text">Stage password (optional)</span>
      </label>
      <input type="password" id="password" placeholder="Enter a password to protect your stage" name="password" required autocomplete="off" class="input w-full">
      <p class="label">
        <span class="label-text-alt">You need to give users this password so they can join your stage</span>
      </p>
    </div>
    <div class="my-2">
      <label for="private" class="label">
        <span class="label-text">Invite only</span>
        <input type="checkbox" name="private" id="private" class="toggle toggle-primary" />
      </label>
      <p class="label">
        <span class="label-text-alt">Turning this on will only allow users you invite to join the stage. The stage will also be hidden from Discover.</span>
      </p>
    </div>
    <div class="my-2">
      <label for="color" class="label">
        <span class="label-text">Stage color</span>
        <div class="flex items-center gap-2">
        <input bind:value={selectedColor} type="color" name="color" id="color" title="Select a color for your stage" />
        <button type="submit" on:click={generateRandomColor} class="btn btn-square btn-sm"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
</svg></button>
        </div>
      </label>
      <p class="label">
        <span class="label-text-alt">Make sure to select a bright color to contrast the background!</span>
      </p>
    </div>
    <div class="my-2">
      <button class="btn-block btn" bind:this={createStageBtn}>Create stage</button>
    </div>
  </form>
{/if}
