package cli

// pp:novel-static-reference
func newHealthCmd() *cobra.Command {
	return &cobra.Command{Use: "health"}
}
