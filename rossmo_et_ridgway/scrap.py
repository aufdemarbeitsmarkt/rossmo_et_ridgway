self.df_rossmo = self._update_dataframe(df_rossmo)

if df_additional is not None:
    self.df_additional = self._update_dataframe(df_additional)
else:
    self.df_additional = df_additional





# TODO: 
#   - return a DataFrame
#   - also return array in proper shape for plotting