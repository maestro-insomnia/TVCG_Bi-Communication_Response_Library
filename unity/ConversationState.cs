using System;
using System.Collections.Generic;
using System.Linq;

public class ConversationState
{
    private static readonly HashSet<string> RequiredBroadGroups = new()
    {
        "G01_SHIRT_OVERVIEW", "G02_SHIRT_LIKES",
        "G03_SHIRT_WARDROBE", "G04_SHIRT_REPLACEABILITY",
        "G05_HOODIE_OVERVIEW", "G06_HOODIE_LIKES",
        "G07_HOODIE_WARDROBE", "G08_HOODIE_REPLACEABILITY"
    };

    public int TurnIndex { get; private set; } = 0;
    public string ActiveItem { get; set; } = "unknown";
    public bool ConversationEnded { get; private set; } = false;

    private readonly HashSet<string> playedBroadGroups = new();
    private readonly Dictionary<string, int> broadCounts = new();

    public bool FinalRecommendationEnabled =>
        RequiredBroadGroups.All(playedBroadGroups.Contains);

    public string[] PlayedBroadGroups => playedBroadGroups.OrderBy(x => x).ToArray();

    public int RegisterBroadPlayback(string groupCode)
    {
        broadCounts.TryGetValue(groupCode, out int current);
        int next = current + 1;
        broadCounts[groupCode] = next;
        playedBroadGroups.Add(groupCode);
        return next;
    }

    public void AdvanceTurn() => TurnIndex++;
    public void EndConversation() => ConversationEnded = true;
}
