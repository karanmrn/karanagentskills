package cli

func Execute() {
	rootCmd.AddCommand(newHealthCmd())
}
