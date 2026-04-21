export const dataReducer = (state: any, action: any) => {
  if (action.type === 'set-data') {
    return {
      ...state,
      loadingState: false,
      columnKeyVers: state.columnKeyVers + 1,
      data: action.data,
    };
  } else if (action.type === 'set-loader') {
    return {
      ...state,
      loadingState: true,
      columnKeyVers: state.columnKeyVers + 1,
    };
  } else {
    return state;
  }
};

export const filterReducer = ({ action, setFilterComKey }: any) => {
  if (action.isReset) {
    setFilterComKey((prevFilterComKey: any) => prevFilterComKey + 1);
  }

  return {
    filters: action.filterData,
  };
};
