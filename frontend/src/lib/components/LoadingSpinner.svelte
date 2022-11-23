<script>
  export let w = "64px"
  export let h = "64px"
  export let t = "8px"
</script>

<div style="width: {w}; height: {h}; border-width: {t}">
</div>

<style>
  div {
    @apply transition-all duration-500 rounded-full;
    border-color: theme("colors.base-100");
    border-top-color: theme("colors.primary");
    animation: spin .75s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
</style>
