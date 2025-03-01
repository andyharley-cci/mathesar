<script lang="ts">
  import { get } from 'svelte/store';
  import {
    faFilter,
    faSort,
    faListAlt,
  } from '@fortawesome/free-solid-svg-icons';
  import {
    getTable,
    fetchTableRecords,
  } from '@mathesar/stores/tableData';
  import URLQueryHandler from '@mathesar/utils/urlQueryHandler';
  import type {
    TableColumnStore,
    TableRecordStore,
    TableOptionsStore,
    TableDisplayStores,
  } from '@mathesar/stores/tableData';
  import { States } from '@mathesar/utils/api';
  import { Button, Icon } from '@mathesar-components';
  import DisplayOptions from './display-options/DisplayOptions.svelte';
  import Header from './Header.svelte';
  import Body from './Body.svelte';
  import type { ItemInfo } from './virtual-list/listUtils';

  export let database: string;
  export let id: unknown;
  $: identifier = id as number;

  /**
   * idKey is only modified after table display properties
   * are set.
   *
   * It is used for recreating the virtual list instance, so
   * it should only be set in the same tick as the required
   * props for virtual list.
   */
  let idKey = id as number;

  let columns: TableColumnStore;
  let records: TableRecordStore;
  let options: TableOptionsStore;
  let tableBodyRef: Body;

  let columnPosition: TableDisplayStores['columnPosition'];
  let horizontalScrollOffset: TableDisplayStores['horizontalScrollOffset'];
  let scrollOffset: TableDisplayStores['scrollOffset'];
  let groupIndex: TableDisplayStores['groupIndex'];
  let showDisplayOptions: TableDisplayStores['showDisplayOptions'];

  let animateOpts = false;

  function setStores(_database: string, _id: number) {
    const opts = URLQueryHandler.getTableConfig(_database, _id);
    const table = getTable(_database, _id, opts);
    columns = table.columns;
    records = table.records;
    options = table.options;

    columnPosition = table.display.columnPosition;
    horizontalScrollOffset = table.display.horizontalScrollOffset;
    scrollOffset = table.display.scrollOffset;
    groupIndex = table.display.groupIndex;
    showDisplayOptions = table.display.showDisplayOptions;

    animateOpts = false;
    idKey = _id;
  }

  $: setStores(database, identifier);

  function refetch(event: { detail: ItemInfo }) {
    const itemInfo = event.detail;
    const optInfo = get(options);
    const recordInfo = get(records);

    const offset = Math.max(itemInfo.startIndex - 20, 0);
    let limit = itemInfo.stopIndex - itemInfo.startIndex + 26;
    if (recordInfo.totalCount !== null
        && offset + limit > recordInfo.totalCount) {
      limit = recordInfo.totalCount - offset;
    }
    options.set({
      ...optInfo,
      limit,
      offset,
    });

    void fetchTableRecords(database, identifier);
  }

  function reload(event: { detail: { resetPositions?: boolean } }) {
    const resetPositions = event?.detail?.resetPositions || false;
    const optInfo = get(options);
    options.set({
      ...optInfo,
      limit: 50,
      offset: 0,
    });
    void fetchTableRecords(database, identifier, true);
    URLQueryHandler.setTableOptions(database, identifier, $options);
    if (tableBodyRef) {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call
      tableBodyRef.reloadPositions(resetPositions);
    }
  }

  function openDisplayOptions() {
    animateOpts = true;
    showDisplayOptions.set(true);
  }

  function closeDisplayOptions() {
    animateOpts = true;
    showDisplayOptions.set(false);
  }
</script>

<div class="actions-pane">
  <Button appearance="plain" on:click={openDisplayOptions}>
    <Icon data={faFilter} size="0.8em"/>
    <span>
      Filters
      {#if $options.filter?.filters?.length > 0}
        ({$options.filter?.filters?.length})
      {/if}
    </span>
  </Button>

  <Button appearance="plain" on:click={openDisplayOptions}>
    <Icon data={faSort}/>
    <span>
      Sort
      {#if $options.sort?.size > 0}
        ({$options.sort?.size})
      {/if}
    </span>
  </Button>

  <Button appearance="plain" on:click={openDisplayOptions}>
    <Icon data={faListAlt}/>
    <span>
      Group
      {#if $options.group?.size > 0}
        ({$options.group?.size})
      {/if}
    </span>
  </Button>

  {#if $columns.state === States.Loading}
    | Loading table

  {:else if $columns.state === States.Error}
    | Error in loading table: {$columns.error}
  {/if}

  {#if $records.state === States.Loading}
    | Loading records

  {:else if $records.state === States.Error}
    | Error in loading records: {$records.error}
  {/if}
</div>

<div class="table-data" class:animate-opts={animateOpts}
      class:has-display-opts={$showDisplayOptions}>
  <div class="display-options-pane">
    {#if $showDisplayOptions}
      <DisplayOptions
        columns={$columns}
        bind:sort={$options.sort}
        bind:group={$options.group}
        bind:filter={$options.filter}
        on:reload={reload}
        on:close={closeDisplayOptions}/>
    {/if}
  </div>

  <div class="table-content">
    {#if $columns.data.length > 0}
      <Header columns={$columns}
              bind:sort={$options.sort}
              bind:group={$options.group}
              isResultGrouped={!!$records.groupData}
              bind:columnPosition={$columnPosition}
              bind:horizontalScrollOffset={$horizontalScrollOffset}
              on:reload={reload}/>

      <Body bind:this={tableBodyRef} id={idKey}
            columns={$columns} data={$records.data}
            groupData={$records.groupData}
            groupIndex={$groupIndex}
            columnPosition={$columnPosition}
            bind:scrollOffset={$scrollOffset}
            bind:horizontalScrollOffset={$horizontalScrollOffset}
            on:refetch={refetch}/>
    {/if}
  </div>
</div>

<div class="status-pane">
  
</div>

<style global lang="scss">
  @import "TableView.scss";
</style>
