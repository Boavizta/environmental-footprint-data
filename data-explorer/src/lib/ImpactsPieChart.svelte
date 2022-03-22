<script lang="ts">
    export let scope2={result:-1, lines:0};
    export let scope3={result:-1, lines:0};
    export let selectedRowsNumber=0;
    import { _ } from 'svelte-i18n';

</script>

<div id="stats">
    <div class="camembert-left">
    </div>
</div>
    {#if scope2.result!=-1}
        <p>
        moyenne du scope 2 : {scope2.result/scope2.lines} sur {scope2.lines} ligne(s)</p>
    {:else}
        <p>moyenne du scope 2 : pas de calcul</p>
    {/if}

{#if scope3.result!=-1}
    <p>
        moyenne du scope 3 : {scope3.result/scope3.lines} sur {scope3.lines} ligne(s)</p>
{:else}
    <p>moyenne du scope 3 : pas de calcul</p>
{/if}

