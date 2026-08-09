using System;

[Serializable]
public class BcRouteRequest
{
    public string protocolVersion = "6.3";
    public int turnIndex;
    public bool finalRecommendationEnabled;
    public string inputMode;     // typed | asr
    public string activeItem;    // first_top | second_top | both | unknown
    public string rawInputText;
    public string[] playedBroadGroups;
    public RecentTurn[] recentTurns;
}

[Serializable]
public class RecentTurn
{
    public int turnIndex;
    public string participantText;
    public string correctedParticipantText;
    public string utteranceType;
    public string routeCode;
}
