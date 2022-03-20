<script lang="ts">
    export let disabledSearchButton;
    export let onClick
    import { _ } from 'svelte-i18n';

</script>

<button disabled="{disabledSearchButton}" on:click={onClick}>{$_('index.calculate')}</button>
