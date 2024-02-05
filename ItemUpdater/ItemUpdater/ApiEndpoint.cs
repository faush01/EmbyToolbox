using MediaBrowser.Common.Configuration;
using MediaBrowser.Common;
using MediaBrowser.Controller.Configuration;
using MediaBrowser.Controller.Library;
using MediaBrowser.Model.IO;
using MediaBrowser.Model.Logging;
using MediaBrowser.Model.Serialization;
using MediaBrowser.Model.Services;
using System;
using System.Collections.Generic;
using System.Text;
using MediaBrowser.Controller.Persistence;
using MediaBrowser.Controller.Entities;
using System.Threading;
using System.Collections;

namespace ItemUpdater
{

    public class UpdateDetails
    {
        public string Id { get; set; }
        public string Type { get; set; }
        public string Value { get; set; }
    }

    public class UpdateItemsDetails
    {
        public List<UpdateDetails> UpdateActions { get; set; } = new List<UpdateDetails>();
    }

    // http://localhost:8096/emby/item_updater/update
    [Route("/item_updater/update", "POST", Summary = "Update Item")]
    //[Authenticated]
    public class UpdateItems : UpdateItemsDetails, IReturn<Object>
    {
    }

    // http://localhost:8096/emby/item_updater/ping
    [Route("/item_updater/ping", "GET", Summary = "PingTest")]
    //[Authenticated]
    public class PingTest : IReturn<Object>
    {
    }

    public class ApiEndpoint : IService
    {
        private readonly ILogger _logger;
        private readonly ILibraryManager _libraryManager;
        private readonly IJsonSerializer _jsonSerializer;
        private readonly IItemRepository _itemRepository;

        public ApiEndpoint(ILogManager logger,
            ILibraryManager libraryManager,
            IJsonSerializer jsonSerializer,
            IItemRepository itemRepository)
        {
            _logger = logger.GetLogger("ItemUpdater - ApiEndpoint");
            _libraryManager = libraryManager;
            _jsonSerializer = jsonSerializer;
            _itemRepository = itemRepository;
        }

        public object Get(PingTest request)
        {
            Dictionary<string, object> responce = new Dictionary<string, object>();
            responce["message"] = "ping result";
            return responce;
        }

        public object Post(UpdateItems request)
        {
            string some_data = _jsonSerializer.SerializeToString(request);
            _logger.Info("Submitted config data : " + some_data);

            int total_updated = 0;
            List<BaseItem> updated_items = new List<BaseItem>();
            foreach(UpdateDetails cr in request.UpdateActions)
            {
                bool item_updated = false;
                long emby_id = long.Parse(cr.Id);
                BaseItem item = _libraryManager.GetItemById(emby_id);

                if(cr.Type.Equals("CommunityRating", StringComparison.CurrentCultureIgnoreCase))
                {
                    float rating = float.Parse(cr.Value);
                    item.CommunityRating = rating;
                    item_updated = true;
                }

                if(item_updated)
                {
                    updated_items.Add(item);
                    total_updated++;
                }
            }
            
            if(updated_items.Count > 0)
            {
                CancellationToken token = CancellationToken.None;
                _itemRepository.SaveItems(updated_items, token);
            }

            Dictionary<string, object> responce = new Dictionary<string, object>();
            responce["message"] = "items updated: " + total_updated;
            return responce;
        }


    }
}
